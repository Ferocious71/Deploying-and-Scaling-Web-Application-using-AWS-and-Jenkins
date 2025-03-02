FROM node:18

WORKDIR /app

COPY package.json .  
RUN npm install --fetch-retries=5 --fetch-timeout=60000

COPY . .  

CMD ["node", "index.js"]
