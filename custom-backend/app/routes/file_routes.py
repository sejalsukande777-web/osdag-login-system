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
        # file exists but it's someone else's. using 404 here instead of 403 on
        # purpose - if I returned 403 that basically confirms "yeah this file_id
        # is real, just not yours" which tells an attacker the id is valid.
        # same 404 either way so they can't tell the difference
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")

    return file
