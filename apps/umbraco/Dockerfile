FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

ARG UMBRACO_VERSION=18.2.0

RUN dotnet new install Umbraco.Templates::${UMBRACO_VERSION}

WORKDIR /src
RUN dotnet new umbraco -n UmbracoApp -o UmbracoApp --no-restore
RUN dotnet publish UmbracoApp/UmbracoApp.csproj -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final

WORKDIR /app
COPY --from=build /app/publish .

RUN mkdir -p /app/umbraco/Data /app/umbraco/Logs /app/wwwroot/media

ENV ASPNETCORE_URLS=http://+:8080 \
    ASPNETCORE_ENVIRONMENT=Production

EXPOSE 8080

ENTRYPOINT ["dotnet", "UmbracoApp.dll"]
