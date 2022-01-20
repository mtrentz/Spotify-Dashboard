from .auth_views import BaseAuthView


class SearchView(BaseAuthView):
    def search_album_id(self, album_sp_id):
        """
        Search album id in spotify
        """
        album = self.sp.album(album_sp_id)
        return album
