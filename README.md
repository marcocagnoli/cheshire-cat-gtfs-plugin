# What is this?
This is a plugin (tool) for the [Cheshire Cat Project](https://github.com/pieroit/cheshire-cat), allowing the Cat to retrieve real time transit data from a GTFS feed.

# Install
Download the **gtfs** folder into the **plugin** one.

# Configuration
To retrieve information, the plugin use the [Transit Land](https://www.transit.land/) API. Transit Land collects GTFS feeds worldwide, so you can configure the cat to give transit information - potentially - from every city in the world. Actually you can configure only one city at time. In order to use the plugin, you will need:
- A Transit Land API key (a free plan is available).
- A **Onestop ID**, a unique ID for a GTFS feed (ideally, a feed should cover a city or a region). Use their search engine to find out the right Onestop ID for you. Please, note that several feeds will not contain real time data, in such a situation the cat will provide only scheduled timetables.

Write these two values into the gtfs.py file.

# Usage
Ask the cat something like "*I'm at bus stop 74637, can you tell me next buses arrivals?*". For example, in Rome, following values are valid stop codes:
- 74637
- 70100
- 72962

# Output

