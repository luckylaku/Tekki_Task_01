from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now, timedelta
from .models import Product, ProductRetrieval
from .serializers import ProductSerializer
from django.db import models 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        ProductRetrieval.objects.create(product=instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_products(self, request):
        timeframe = request.query_params.get('timeframe', 'all')
        now_time = now()
        if timeframe == 'day':
            start_time = now_time - timedelta(days=1)
        elif timeframe == 'week':
            start_time = now_time - timedelta(weeks=1)
        else:
            start_time = None

        retrievals = ProductRetrieval.objects.all()
        if start_time:
            retrievals = retrievals.filter(retrieved_at__gte=start_time)

        top_products = (
            retrievals.values('product')
            
            .annotate(retrieval_count=models.Count('product'))
            .order_by('-retrieval_count')[:5]
        )

        top_products_data = []
        for entry in top_products:
            product = Product.objects.get(id=entry['product'])
            product_data = ProductSerializer(product).data
            product_data['retrieval_count'] = entry['retrieval_count']
            top_products_data.append(product_data)

        return Response(top_products_data, status=status.HTTP_200_OK)
