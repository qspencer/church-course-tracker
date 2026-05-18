# Multi-stage build for Angular frontend.
#
# Note: the production deployment does NOT use this Dockerfile - it is
# built by .github/workflows/deploy.yml (`ng build --configuration=
# production`) and pushed to S3 + CloudFront. This Dockerfile is kept
# for local prod-like testing via docker/docker-compose.yml.
#
# Two real bugs fixed in this file 2026-05-18 (P1 #20 from the May-18 eval):
#   - `npm ci --only=production` skipped @angular/cli (it's a devDependency),
#     so the build step had no `ng` binary. Use `npm ci` (full install).
#   - `npm run build --prod` passes `--prod` to npm (which is a no-op since
#     npm 7) rather than to ng build. Use `-- --configuration=production`.
FROM node:20-alpine AS build

WORKDIR /app

# Copy lockfile + manifest first so layer caching reuses `npm ci` when
# only source changes (not deps).
COPY package*.json ./

# Full install (dev deps include @angular/cli which the build needs).
RUN npm ci

# Copy source and build with the correct Angular production configuration.
COPY . .
RUN npm run build -- --configuration=production --base-href=/churchcoursetracker/

# Production stage - serve the built bundle through nginx.
FROM nginx:alpine

COPY --from=build /app/dist/church-course-tracker /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
