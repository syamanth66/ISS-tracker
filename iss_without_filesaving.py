import requests
import time
import math
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# Haversine function to calculate distance between two coordinates
def haversine(lat1, lon1, lat2, lon2, alt = 0):
    R = 6371 + alt # Radius of the Earth in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in km

# Initial coordinates (example)
lat1, lon1 = 16.4328, 80.7697  # Kankipadu, Krishna
#file_path = r"C:\Users\Syama\OneDrive\Documents\iss.txt"  # File to save data
poll_interval = 1  # Polling interval in seconds
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
n = 10  # Timeout for API requests

# Set up the plot with black background
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
fig.patch.set_facecolor('black')  # Set figure background to black
ax.set_facecolor('black')  # Set axes background to black

# Map features
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.LAND, edgecolor='black')  # Land in light gray
ax.add_feature(cfeature.OCEAN, edgecolor='black')  # Ocean in dark blue
ax.add_feature(cfeature.COASTLINE, edgecolor='black')  # Coastline in white
ax.add_feature(cfeature.BORDERS, edgecolor='black')  # Borders in white

# Add gridlines
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

gl = ax.gridlines(draw_labels=True, color='green', linewidth=1.5)
gl.xlabels_top = False  # Disable top labels
gl.ylabels_right = False  # Disable right labels
gl.xformatter = LONGITUDE_FORMATTER  # Format longitude labels
gl.yformatter = LATITUDE_FORMATTER  # Format latitude labels
gl.xlabel_style = {'size': 12, 'color': 'white'}  # Style for x-axis labels
gl.ylabel_style = {'size': 12, 'color': 'white'}  # Style for y-axis labels

# Add axis labels
ax.set_title("Location of International Space Station", fontsize=15, color='white', pad=10)
ax.text(0.5, -0.07, "Longitude", transform=ax.transAxes,
        ha='center', va='center', fontsize=15, color='white')
ax.text(-0.1, 0.5, "Latitude", transform=ax.transAxes, 
        rotation='vertical', ha='center', va='center', 
        fontsize=15, color='white')

plt.ion()  # Turn on interactive mode

# Initialize data for plotting
lat, lon = [0], [0]
iss_scatter = ax.scatter([], [], s=9, color='red', label='ISS')
target_marker = ax.scatter(lon1, lat1, color='blue', marker='s', label='Target')
plt.legend()
footer = plt.figtext(0.5, 0.02, '', ha='center', va='center', fontsize=15, color='yellow')
pager = plt.figtext(0.5, 0.98, '', ha='center', va='center', fontsize=15, color='green')
footer_text = ''

#timelist
timel = [0]
speedl = []
count = 0

# Function to poll data from the API
def poll_data():
    global footer_text,count
    while True:
        try:
            res = requests.get('http://api.open-notify.org/iss-now.json', headers=headers, timeout=n)
            data = res.json()
            lat2 = float(data['iss_position']['latitude'])
            lon2 = float(data['iss_position']['longitude'])
            tim = float(data['timestamp'])
            print(f"New position: Latitude {lat2}, Longitude {lon2}")

            # Calculate distance to the reference point
            distance = haversine(lat1, lon1, lat2, lon2)
            current_time = datetime.now()
            print(f"Distance between ISS and Kankipadu: {distance:.4f} km\n")

            # Update plot data
            lat.append(lat2)
            lon.append(lon2)
            timel.append(tim)
            iss_scatter.set_offsets(list(zip(lon, lat)))

            #finding speed of ISS
            pastlat = lat[-2]
            pastlon = lon[-2]
            currlat = lat[-1]
            currlon = lon[-1]
            dist_travelled_unit = haversine(pastlat,pastlon,currlat,currlon,410)
            timetaken = timel[-1]-timel[-2] 
            speed = (dist_travelled_unit/timetaken)*60*60
            speedl.append(speed)
            totpolls = len(speedl)
            avgspeed = sum(speedl)/totpolls
            count += 1 #counter to remove first element from speed list due to the fact that first polled speed is inaccurate 
            if count == 3:
                del speedl[0]


            # Update text
            footer_text = f'{current_time} --- Distance from ISS to Kankipadu: {distance:.2f} km, avg speed : {avgspeed:.2f} Kmph'
            print(f'avg speed : {avgspeed:.2f} Kmph')
            pager_text = f'Current location: [Latitude: {lat2}, Longitude: {lon2}]'
            footer.set_text(footer_text)
            pager.set_text(pager_text)
            footer.set_color('yellow')
            pager.set_color('green')

            # Save data to file
            #with open(file_path, 'a') as issfile:
                #issfile.write(f"{current_time}, {distance:.2f} km, {lat2}, {lon2}\n")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            footer.set_text(footer_text)
            footer.set_color('red')
            pager.set_color('red')
            pager.set_text('--- Reconnecting... ---')

        plt.pause(poll_interval)

poll_data()
