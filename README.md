# Spotify-Dashboard

Keep up to date on your Spotify listening activity! Get a general overview of the tracks and artists you've listened to in the recent past as well as your year in review!

Authorizing the app will refresh your latest activity automatically. You're also able to upload your past history by requesting your data from Spotify's official website.

![App Preview](https://i.imgur.com/iRAIW8z.png)

## Setting up

To start using the app you'll have to first request your own API keys from Spotify.

1. Go to the [Developers Dashboard](https://developer.spotify.com/dashboard/login)
2. Login and create a new app
3. Go to _Edit Settings_
4. To avoid possible errors add all these **Redirect URIs** and save it  
   http://localhost:8080/  
   http://localhost:8080  
   http://127.0.0.1:8080/  
   http://127.0.0.1:8080  
5. On your app's main page copy your **Client ID** and **Client Secret**

After that, clone this repo and edit the `docker-compose.yml` file at the very top with your app's info:

```yaml
x-common-variables: &common-variables
...
  SPOTIPY_CLIENT_ID: 123abc345...
  SPOTIPY_CLIENT_SECRET: 111aaa222...
  SPOTIPY_REDIRECT_URI: http://localhost:8080/
  LOGIN_USERNAME: admin # This will be used to access the app page
  LOGIN_PASSWORD: admin
  # Frequency which your recently played tracks will be checked in MINUTES (1-59). Defaults to 15.
  RECENTLY_PLAYED_JOB_PERIODICITY: 5
...
```

## Installing

To build the app:
```
docker-compose build
```

After everything is done:
```
docker-compose up -d
```

## Getting your data

The first step is Authorizing your app to access your Spotify Data.

To do that click on the **Authorize** button that should show up in the navbar after logging in the app's main page at http://localhost:8080/.

Accept everything and done! The app should automatically refresh every few minutes with your listening activity! To force it you can click on the refresh button at the far left on the _Your Recent Activity_ card.

To get your past history you can request it directly through Spotify. For that login into your [Account Overview](https://www.spotify.com/us/account/overview/), go to _Privacy Settings_ and ask to **download your data**. It might take a few days, but Spotify will notice you via email.

After receiving your data, you can upload all your StreamingHistory.json files directly through the app's main page. Just click on the **Upload History** button in the navbar and follow the instructions there. Keep in mind that this will take a while to run, you can check if everything is going according to plan by checking the docker logs. For that, run `docker-compose logs -f`.
