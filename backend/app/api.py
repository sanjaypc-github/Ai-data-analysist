"""
API endpoints for the Autonomous Data Analyst Agent
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
from pathlib import Path
import logging
import uuid
import traceback

from .schemas import (
    UploadResponse, AskRequest, AskResponse, TaskStatusResponse,
    ReportResponse, TaskStatus
)
from .utils import (
    save_uploaded_file, get_dataset_path, inspect_csv,
    create_task_dir, save_task_metadata, load_task_metadata,
    update_task_status, get_task_output_files
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a CSV dataset for analysis (validation only, no auto-preprocessing)
    
    Args:
        file: CSV file upload
    
    Returns:
        UploadResponse with dataset_id and metadata
    """
    try:
        from .data_validator import analyze_data_quality
        import pandas as pd
        
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read file content
        content = await file.read()
        
        # Save file
        dataset_id, file_path = save_uploaded_file(content, file.filename)
        logger.info(f"Uploaded dataset {dataset_id}: {file.filename}")
        
        # Just validate encoding and readability (no preprocessing)
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Dataset loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read CSV: {str(e)}"
            )
        
        # Inspect CSV
        metadata = inspect_csv(file_path)
        
        return UploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            rows=metadata["rows"],
            columns=metadata["columns"],
            dtypes=metadata["dtypes"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Submit a natural language question for analysis
    
    Args:
        request: AskRequest with dataset_id and question
    
    Returns:
        AskResponse with task_id and generated code
    """
    try:
        # Import here to avoid circular dependencies
        from .llm_client import generate_code_for_question
        from .safety import is_safe_pandas
        from .sandbox_runner import run_code_in_sandbox
        
        # Validate dataset exists
        try:
            dataset_path = get_dataset_path(request.dataset_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_id} not found")
        
        logger.info(f"Processing question for dataset {request.dataset_id}: {request.question}")
        
        # Generate code using LLM
        generated_code = generate_code_for_question(
            question=request.question,
            dataset_path=dataset_path,
            context=request.context,
            enable_visualization=request.enable_visualization
        )
        
        logger.info(f"Generated code:\n{generated_code}")
        
        # Validate code safety
        is_safe, reason = is_safe_pandas(generated_code)
        
        if not is_safe:
            logger.warning(f"Unsafe code detected: {reason}")
            raise HTTPException(
                status_code=400,
                detail=f"Generated code failed safety validation: {reason}"
            )
        
        logger.info("Code passed safety validation")
        
        # Create task
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task_dir = create_task_dir(task_id)
        
        # Save generated code
        code_path = task_dir / "generated_code.py"
        with open(code_path, "w") as f:
            f.write(generated_code)
        
        # Save prompt for reproducibility
        prompt_path = task_dir / "prompt.txt"
        with open(prompt_path, "w") as f:
            f.write(f"Question: {request.question}\n")
            f.write(f"Dataset: {request.dataset_id}\n")
            f.write(f"Context: {request.context or 'None'}\n")
        
        # Initialize task metadata
        task_metadata = {
            "task_id": task_id,
            "dataset_id": request.dataset_id,
            "question": request.question,
            "context": request.context,
            "generated_code": generated_code,
            "status": TaskStatus.RUNNING.value,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "stdout": None,
            "stderr": None,
            "result_files": [],
            "error_message": None
        }
        save_task_metadata(task_id, task_metadata)
        
        # Execute code in sandbox (async in background)
        # TODO: Make this truly async with background tasks
        try:
            result = run_code_in_sandbox(
                code=generated_code,
                dataset_path=dataset_path,
                task_id=task_id
            )
            
            # Update task with results
            update_task_status(task_id, {
                "status": TaskStatus.COMPLETED.value if result["success"] else TaskStatus.FAILED.value,
                "completed_at": datetime.now().isoformat(),
                "stdout": result.get("stdout", ""),
                "stderr": result.get("stderr", ""),
                "result_files": get_task_output_files(task_id),
                "error_message": result.get("error", None)
            })
            
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}\n{traceback.format_exc()}")
            update_task_status(task_id, {
                "status": TaskStatus.FAILED.value,
                "completed_at": datetime.now().isoformat(),
                "error_message": str(e)
            })
        
        return AskResponse(
            task_id=task_id,
            dataset_id=request.dataset_id,
            question=request.question,
            generated_code=generated_code,
            status=TaskStatus.RUNNING
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ask failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get task execution status and results
    
    Args:
        task_id: Task identifier
    
    Returns:
        TaskStatusResponse with execution details
    """
    try:
        metadata = load_task_metadata(task_id)
        
        return TaskStatusResponse(
            task_id=metadata["task_id"],
            dataset_id=metadata["dataset_id"],
            question=metadata["question"],
            status=metadata["status"],
            generated_code=metadata["generated_code"],
            created_at=metadata["created_at"],
            completed_at=metadata.get("completed_at"),
            stdout=metadata.get("stdout"),
            stderr=metadata.get("stderr"),
            result_files=metadata.get("result_files", []),
            error_message=metadata.get("error_message")
        )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/report/{task_id}", response_model=ReportResponse)
async def get_report(task_id: str):
    """
    Get or generate HTML report for task
    
    Args:
        task_id: Task identifier
    
    Returns:
        ReportResponse with report availability and path
    """
    try:
        from .report_generator import generate_report
        from .utils import get_data_dirs
        
        # Check if task exists
        metadata = load_task_metadata(task_id)
        
        # Check if report already exists
        dirs = get_data_dirs()
        report_path = dirs["tasks"] / task_id / f"{task_id}.html"
        
        if not report_path.exists():
            # Generate report
            logger.info(f"Generating report for task {task_id}")
            generate_report(task_id, metadata)
        
        if report_path.exists():
            return ReportResponse(
                task_id=task_id,
                report_available=True,
                report_path=str(report_path),
                message="Report generated successfully"
            )
        else:
            return ReportResponse(
                task_id=task_id,
                report_available=False,
                message="Report generation failed or task not completed"
            )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/report/{task_id}/download")
async def download_report(task_id: str):
    """
    Download HTML report for task
    
    Args:
        task_id: Task identifier
    
    Returns:
        FileResponse with HTML report
    """
    try:
        from .report_generator import generate_report
        from .utils import get_data_dirs
        
        # Check if task exists
        metadata = load_task_metadata(task_id)
        
        # Check if report already exists
        dirs = get_data_dirs()
        report_path = dirs["tasks"] / task_id / f"{task_id}.html"
        
        if not report_path.exists():
            # Generate report
            logger.info(f"Generating report for task {task_id}")
            generate_report(task_id, metadata)
        
        if report_path.exists():
            return FileResponse(
                path=str(report_path),
                media_type="text/html",
                filename=f"analysis_report_{task_id}.html"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Report generation failed or task not completed"
            )
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    except Exception as e:
        logger.error(f"Report download failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Report download failed: {str(e)}")


@router.get("/task/{task_id}/file/{filename}")
async def get_task_file(task_id: str, filename: str):
    """
    Download output files (CSV, PNG, etc.) from task
    
    Args:
        task_id: Task identifier
        filename: Name of the file to download
    
    Returns:
        FileResponse with the requested file
    """
    try:
        from .utils import get_data_dirs
        
        # Validate task exists
        dirs = get_data_dirs()
        task_output_dir = dirs["tasks"] / task_id / "outputs"
        
        if not task_output_dir.exists():
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Sanitize filename to prevent directory traversal
        safe_filename = Path(filename).name
        file_path = task_output_dir / safe_filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # Determine media type
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.txt': 'text/plain'
        }
        suffix = file_path.suffix.lower()
        media_type = media_types.get(suffix, 'application/octet-stream')
        
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=safe_filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File download failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")


@router.get("/dataset/{dataset_id}/quality")
async def get_data_quality(dataset_id: str):
    """
    Get data quality report for uploaded dataset (always uses ORIGINAL file)
    
    Args:
        dataset_id: Dataset identifier
    
    Returns:
        Quality report with missing values, duplicates, etc.
    """
    try:
        from .data_validator import analyze_data_quality
        import pandas as pd
        
        # Get ORIGINAL dataset path (not preprocessed)
        dataset_path = get_dataset_path(dataset_id, prefer_processed=False)
        
        # Load dataset
        df = pd.read_csv(dataset_path)
        logger.info(f"Analyzing quality of ORIGINAL file: {dataset_path}")
        
        # Analyze quality
        quality_report = analyze_data_quality(df)
        
        return quality_report
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")
    except Exception as e:
        logger.error(f"Quality analysis failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Quality analysis failed: {str(e)}")


@router.post("/dataset/preprocess")
async def preprocess_dataset(request: dict):
    """
    Preprocess dataset with user-selected strategy
    
    Args:
        request: Dictionary with dataset_id, strategy, and options
    
    Returns:
        Preprocessing results with actions performed
    """
    try:
        from .data_validator import preprocess_dataframe, analyze_data_quality
        from .utils import get_data_dirs
        import pandas as pd
        
        dataset_id = request.get('dataset_id')
        strategy = request.get('strategy', 'auto')
        handle_duplicates = request.get('handle_duplicates', False)
        custom_config = request.get('custom_config', {})
        
        if not dataset_id:
            raise HTTPException(status_code=400, detail="dataset_id is required")
        
        # Get ORIGINAL dataset path (not already preprocessed)
        dataset_path = get_dataset_path(dataset_id, prefer_processed=False)
        
        # Load dataset
        df = pd.read_csv(dataset_path)
        logger.info(f"Loaded ORIGINAL dataset {dataset_id}: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Apply preprocessing based on strategy
        actions = []
        
        # Handle custom configuration
        if strategy == "custom" and custom_config:
            df_processed = df.copy()
            for col_name, config in custom_config.items():
                if col_name not in df_processed.columns:
                    continue
                
                col_strategy = config.get('strategy')
                missing_count = df_processed[col_name].isnull().sum()
                
                if missing_count == 0:
                    continue
                
                if col_strategy == "median":
                    median_val = df_processed[col_name].median()
                    df_processed[col_name].fillna(median_val, inplace=True)
                    actions.append(f"Filled {missing_count} missing in '{col_name}' with median ({median_val:.2f})")
                
                elif col_strategy == "mean":
                    mean_val = df_processed[col_name].mean()
                    df_processed[col_name].fillna(mean_val, inplace=True)
                    actions.append(f"Filled {missing_count} missing in '{col_name}' with mean ({mean_val:.2f})")
                
                elif col_strategy == "zero":
                    df_processed[col_name].fillna(0, inplace=True)
                    actions.append(f"Filled {missing_count} missing in '{col_name}' with 0")
                
                elif col_strategy == "mode":
                    if not df_processed[col_name].mode().empty:
                        mode_val = df_processed[col_name].mode()[0]
                        df_processed[col_name].fillna(mode_val, inplace=True)
                        actions.append(f"Filled {missing_count} missing in '{col_name}' with mode ('{mode_val}')")
                
                elif col_strategy == "custom_value":
                    custom_val = config.get('value', '')
                    df_processed[col_name].fillna(custom_val, inplace=True)
                    actions.append(f"Filled {missing_count} missing in '{col_name}' with '{custom_val}'")
                
                elif col_strategy == "forward_fill":
                    df_processed[col_name] = df_processed[col_name].ffill()
                    actions.append(f"Forward-filled {missing_count} missing in '{col_name}'")
                
                elif col_strategy == "backward_fill":
                    df_processed[col_name] = df_processed[col_name].bfill()
                    actions.append(f"Backward-filled {missing_count} missing in '{col_name}'")
                
                elif col_strategy == "drop":
                    # Will be handled later with dropna
                    pass
        
        else:
            # Map strategy names to preprocessing function names
            strategy_map = {
                "drop_rows": "drop",
                "fill_zero": "fill_zero",
                "fill_mean": "fill_mean",
                "fill_median": "auto",  # auto uses median for numeric
                "fill_mode": "fill_mode",
                "fill_forward": "forward",
                "fill_backward": "backward"
            }
            
            mapped_strategy = strategy_map.get(strategy, strategy)
            
            # Special handling for drop_columns
            if strategy == "drop_columns":
                df_processed = df.copy()
                cols_to_drop = []
                for col in df_processed.columns:
                    missing_pct = (df_processed[col].isnull().sum() / len(df_processed)) * 100
                    if missing_pct > 50:
                        cols_to_drop.append(col)
                
                if cols_to_drop:
                    df_processed.drop(columns=cols_to_drop, inplace=True)
                    actions.append(f"Dropped {len(cols_to_drop)} columns with >50% missing: {', '.join(cols_to_drop)}")
                else:
                    actions.append("No columns exceeded 50% missing threshold")
            
            # Special handling for forward/backward fill
            elif strategy == "fill_forward":
                df_processed = df.copy()
                df_processed = df_processed.ffill()
                actions.append(f"Forward-filled all missing values")
            
            elif strategy == "fill_backward":
                df_processed = df.copy()
                df_processed = df_processed.bfill()
                actions.append(f"Backward-filled all missing values")
            
            else:
                # Use existing preprocessing function
                df_processed, strategy_actions = preprocess_dataframe(df, strategy=mapped_strategy)
                actions.extend(strategy_actions)
        
        # Handle duplicates
        if handle_duplicates:
            initial_rows = len(df_processed)
            df_processed.drop_duplicates(inplace=True)
            removed_duplicates = initial_rows - len(df_processed)
            if removed_duplicates > 0:
                actions.append(f"Removed {removed_duplicates} duplicate rows")
        
        # Save preprocessed version
        dirs = get_data_dirs()
        dataset_dir = dirs["uploads"] / dataset_id
        preprocessed_path = dataset_dir / f"processed_{Path(dataset_path).name}"
        
        df_processed.to_csv(preprocessed_path, index=False)
        logger.info(f"Saved preprocessed data to {preprocessed_path}")
        
        # Get new quality report
        new_quality = analyze_data_quality(df_processed)
        
        return {
            'success': True,
            'dataset_id': dataset_id,
            'actions': actions,
            'rows_before': len(df),
            'rows_after': len(df_processed),
            'new_quality': new_quality,
            'preprocessed_path': str(preprocessed_path)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Preprocessing failed: {str(e)}")
