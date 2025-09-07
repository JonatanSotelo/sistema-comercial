FROM node:20-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
ENV VITE_API_BASE=http://backend:8000 \
    CHOKIDAR_USEPOLLING=true

EXPOSE 3000
CMD ["npm","run","dev","--","--host","0.0.0.0","--","--port","3000"]
