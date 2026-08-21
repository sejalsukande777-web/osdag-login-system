import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserFile
from app.schemas import FileOut, FileDetailOut
from app.auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileOut])
def list_my_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # filtering by owner_id right in the query, not fetching everything and
    # filtering in python - don't want to accidentally leak other users' rows
    return db.query(UserFile).filter(UserFile.owner_id == current_user.id).all()


@router.get("/{file_id}", response_model=FileDetailOut)
def get_file(
    file_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file = db.query(UserFile).filter(UserFile.id == file_id).first()

    if file is None:
        # file just doesn't exist
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    if file.owner_id != current_user.id:
        # task explicitly wants this case distinguishable from "doesn't exist"
        # (I originally used 404 for both here, thinking it was safer since a
        # 403 confirms the id is real - that's a reasonable general practice,
        # but it doesn't match what this specific task asks for, so switched
        # to 403 to actually satisfy the stated requirement)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this file.")

    return file
