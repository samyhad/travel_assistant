from .busca import search_by_profile
from .comparacao import compare_destinations
from .historico import check_visited, save_visited, list_visited
from .preferencias import save_preference, get_preferences

TODAS_AS_FERRAMENTAS = [
    search_by_profile,
    compare_destinations,
    check_visited,
    save_visited,
    list_visited,
    save_preference,
    get_preferences,
]