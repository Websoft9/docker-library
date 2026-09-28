FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

ARG UMBRACO_VERSION=18.2.0

RUN dotnet new install Umbraco.Templates@${UMBRACO_VERSION}

WORKDIR /src
RUN dotnet new umbraco -n UmbracoApp -o UmbracoApp --no-restore
COPY src/appsettings.Production.json /src/UmbracoApp/appsettings.Production.json
RUN dotnet publish UmbracoApp/UmbracoApp.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final

ARG UMBRACO_VERSION=18.2.0

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Umbraco packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/umbraco" \
      org.opencontainers.image.title="umbraco" \
      org.opencontainers.image.vendor="Websoft9" \
      org.opencontainers.image.version="${UMBRACO_VERSION}"

WORKDIR /app
COPY --from=build /app/publish .
COPY src/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && mkdir -p /app/umbraco/Data /app/umbraco/Logs /app/umbraco/certs /app/wwwroot/media

ENV ASPNETCORE_URLS="https://+:8443;http://+:8080" \
    ASPNETCORE_ENVIRONMENT=Production

EXPOSE 8080 8443

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
