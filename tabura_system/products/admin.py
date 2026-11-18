from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'stock_status')
    list_filter = ('category',)
    search_fields = ('name',)

    # Keeps the standard dropdown while hiding the add, change, delete, and view icons
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'category':
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False
            formfield.widget.can_view_related = False
        return formfield

    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Out of Stock</span>'
            )
        elif obj.stock <= 5:
            return format_html(
                '<span style="background-color: #ffc107; color: #212529; padding: 4px 10px; border-radius: 4px; font-weight: bold;">Low Stock ({})</span>',
                obj.stock
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 10px; border-radius: 4px;">In Stock ({})</span>',
                obj.stock
            )
    stock_status.short_description = 'Inventory Status'
