FROM node:20-alpine

WORKDIR /app/frontend

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install && \
    npm cache clean --force

# Copy application files
COPY . .

# Ensure node_modules/.bin is executable
RUN chmod -R +x node_modules/.bin

EXPOSE 5173

# Use npm run which properly resolves the vite binary
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

