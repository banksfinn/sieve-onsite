# Use the official Node.js runtime as the base image
FROM node:21 as builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json /app/package.json
COPY yarn.lock /app/yarn.lock

# Install dependencies
RUN yarn install

# Copy the entire application code to the container
COPY ./ /app

# Build the React app for production
RUN yarn build

FROM nginx:latest

COPY --from=builder /app/dist/ /usr/share/nginx/html/
COPY ./nginx.conf.template /etc/nginx/templates/nginx.conf.template

# Copy a custom entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use the custom entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
