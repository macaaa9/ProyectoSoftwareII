FROM php:8.4-cli

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    unzip \
    zip \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Directorio de trabajo
WORKDIR /var/www

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias Laravel
RUN composer install --no-interaction --prefer-dist --optimize-autoloader

# Permisos
RUN chown -R www-data:www-data storage bootstrap/cache

EXPOSE 8000

# Ejecutar Laravel
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]