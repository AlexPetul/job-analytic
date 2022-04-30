FROM node:17.2.0-alpine

COPY package.json /
RUN npm install
COPY . .

CMD ["npm", "start"]