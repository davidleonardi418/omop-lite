FROM alpine:latest

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN apk --no-cache add bash postgresql-client wait4x

USER appuser

# Copy files
COPY --chown=appuser:appgroup scripts /scripts
COPY --chown=appuser:appgroup setup.sh /setup.sh
RUN chmod +x /setup.sh

# Set entrypoint
ENTRYPOINT ["/bin/bash", "/setup.sh"]
