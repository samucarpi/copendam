from .views import dashboard, dashboard_view
from .test_views import (
    admin_dashboard, test_view, add_category, delete_category,
    add_restaurant, delete_restaurant, add_user, delete_user,
    delete_review, clear_all_polls, get_statistics
)

__all__ = [
    'dashboard', 'dashboard_view', 'admin_dashboard', 'test_view',
    'add_category', 'delete_category', 'add_restaurant', 'delete_restaurant',
    'add_user', 'delete_user', 'delete_review', 'clear_all_polls', 'get_statistics'
]