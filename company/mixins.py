from rest_framework import status
from company.views.company import standard_response


class PermissionCheckMixin:
    """
    Mixin for APIViews to perform dynamic permission checks.
    - Superusers (is_superuser=True): Bypass all permission checks.
    - Non-superusers: Checked against user's assigned permissions.
    """
    module_code = None

    def check_permission(self, request, action, module_code=None):
        # Superusers bypass permission checks
        if getattr(request.user, 'is_superuser', False):
            return None

        target_module = module_code or getattr(self, 'module_code', None)
        if not target_module:
            serializer_class = getattr(self, 'serializer_class', None)
            if serializer_class and hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'model'):
                target_module = serializer_class.Meta.model._meta.model_name
            else:
                view_name = self.__class__.__name__
                for suffix in ['ListCreateView', 'DetailView', 'ListView', 'RestoreView', 'ApproveView', 'RejectView', 'View']:
                    if view_name.endswith(suffix):
                        view_name = view_name[:-len(suffix)]
                        break
                target_module = view_name.lower()

        if hasattr(request.user, 'has_permission') and not request.user.has_permission(target_module, action):
            return standard_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="You do not have permission to perform this action."
            )

        return None
