from flask import jsonify, session, render_template
from db_utils import get_ap_info, get_all_aps

def wifi_ap_utils(ap_id):
    ap_info = get_ap_info(ap_id)

    if ap_info:
        return render_template('wifi_ap.html', ap_info=ap_info)
    else:
        return redirect(url_for('route.dashboard'))

def list_aps_utils():
    aps = get_all_aps()

    return render_template('list_aps.html', aps=aps)
