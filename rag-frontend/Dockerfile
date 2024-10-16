# Base image for Node.js
FROM node:16

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package*.json /app/
RUN npm install

# Copy all source code
COPY . /app

# Build the React application
RUN npm run build

# Use nginx to serve the build files
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80
