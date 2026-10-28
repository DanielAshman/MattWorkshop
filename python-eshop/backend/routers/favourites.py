from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_favourite_service, require_authenticated_user
from models.schemas import CatalogItemResponse
from services.favourite_service import FavouriteService, FavouritesFullError

router = APIRouter(prefix="/api/favourites", tags=["favourites"])


@router.get("", response_model=list[CatalogItemResponse])
def list_favourites(
    buyer_id: str = Depends(require_authenticated_user),
    service: FavouriteService = Depends(get_favourite_service),
):
    return service.list_for_user(buyer_id)


@router.put("/{catalog_item_id}", response_model=list[CatalogItemResponse])
def add_favourite(
    catalog_item_id: int,
    buyer_id: str = Depends(require_authenticated_user),
    service: FavouriteService = Depends(get_favourite_service),
):
    try:
        return service.add(buyer_id, catalog_item_id)
    except FavouritesFullError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{catalog_item_id}", response_model=list[CatalogItemResponse])
def remove_favourite(
    catalog_item_id: int,
    buyer_id: str = Depends(require_authenticated_user),
    service: FavouriteService = Depends(get_favourite_service),
):
    return service.remove(buyer_id, catalog_item_id)
