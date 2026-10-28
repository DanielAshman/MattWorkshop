from db.client import DatabaseClient
from models.schemas import CatalogItemResponse

MAX_FAVOURITES = 5


class FavouritesFullError(Exception):
    pass


class FavouriteService:
    def __init__(self, db: DatabaseClient):
        self.db = db

    def list_for_user(self, buyer_id: str) -> list[CatalogItemResponse]:
        return [
            CatalogItemResponse(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                picture_uri=item.picture_uri,
                catalog_brand_id=item.catalog_brand_id,
                catalog_type_id=item.catalog_type_id,
                brand_name=item.brand_name,
                type_name=item.type_name,
            )
            for item in self.db.list_favourites(buyer_id)
        ]

    def add(self, buyer_id: str, catalog_item_id: int) -> list[CatalogItemResponse]:
        if self.db.get_catalog_item_by_id(catalog_item_id) is None:
            raise ValueError("Product not found")
        added = self.db.add_favourite(buyer_id, catalog_item_id, MAX_FAVOURITES)
        favourites = self.list_for_user(buyer_id)
        if not added and all(item.id != catalog_item_id for item in favourites):
            raise FavouritesFullError(f"You can have up to {MAX_FAVOURITES} favourites")
        return favourites

    def remove(self, buyer_id: str, catalog_item_id: int) -> list[CatalogItemResponse]:
        self.db.remove_favourite(buyer_id, catalog_item_id)
        return self.list_for_user(buyer_id)
