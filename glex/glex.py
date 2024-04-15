from flask import Blueprint, request, render_template
import pgeocode
import googlemaps
import folium
import time

glex_bp = Blueprint('glex', __name__, template_folder="templates")

@glex_bp.route('/glex',methods=['GET','POST'])
def glex():
    if request.method == 'POST':
        result = request.form.get('zipcode')
        nomi = pgeocode.Nominatim('us')
        df = nomi.query_postal_code(result)
        lat_lon = [df['latitude'],df['longitude']]
        key = 'AIzaSyBQrw01btyVL_Y-ioNkQYY8VumySpeBWTo'
        search_radius = 8000
        circle_radius = 1600
        keyword = 'supermarket'
        min_price = 1
        max_price = 3
        gmaps = googlemaps.Client(key)
        m = folium.Map(location=lat_lon,zoom_start=10)
        group = folium.FeatureGroup("Stores")
        list_of_places = gmaps.places(keyword,lat_lon,search_radius, min_price = min_price, max_price = max_price)
        def add_to_group(store):
            folium.Circle(
                location=[store["geometry"]["location"]["lat"],store["geometry"]["location"]["lng"]],
                radius=circle_radius,
                popup=store["name"],
                color=store["icon_background_color"],
                fill=True,
                fill_color=store["icon_background_color"],
            ).add_to(group)

        def next_page(lst):
            for store in list_of_places['results']:
                add_to_group(store)
            while True:
                time.sleep(2)
                try:
                    npt = lst["next_page_token"]
                    lst = gmaps.places(keyword,lat_lon,search_radius,page_token=npt,max_price = max_price,min_price = min_price)
                    for store in list_of_places['results']:
                        add_to_group(store)
                except:
                    break
        inp_zip = True
        next_page(list_of_places)

        group.add_to(m)

        m.get_root().width = "800px"
        m.get_root().height = "600px"
        iframe = m.get_root()._repr_html_()
        return render_template('glex/glex.html', iframe=iframe, inp_zip=inp_zip)
    return render_template('glex/glex.html',iframe=None,inp_zip=False)