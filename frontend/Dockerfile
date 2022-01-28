FROM node:17-alpine
WORKDIR /react

# Copy only package json
COPY package.json .

# Install all dependencies
RUN npm install

# Rebuild on changes to volume
ENV CHOKIDAR_USEPOLLING=true

# Copy rest of the project
COPY . .

# Build it
RUN npm run build