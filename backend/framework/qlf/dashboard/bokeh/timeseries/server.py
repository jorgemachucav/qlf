import holoviews as hv
import pandas as pd
import holoviews.plotting.bokeh
from qlf_models import QLFModels
from holoviews.operation.datashader import datashade
from bokeh.models import HoverTool
from bokeh.plotting import curdoc
import sys
from datetime import datetime

try:
    models = QLFModels()

    renderer = hv.renderer('bokeh')

    args = curdoc().session_context.request.arguments

    def get_arg_string(key):
        try:
            return args.get(key)[0].decode("utf-8")
        except:
            return None

    yaxis = get_arg_string('yaxis')
    amp = get_arg_string('amp')
    start_date = get_arg_string('start')
    start_date = datetime.strptime(start_date, '%Y%m%d').strftime('%Y-%m-%d')
    end_date = get_arg_string('end')
    end_date = datetime.strptime(end_date, '%Y%m%d').strftime('%Y-%m-%d')
    camera = get_arg_string('camera')
    DATASHADE = get_arg_string('datashade')

    outputs = models.get_product_metrics_by_camera(
        yaxis, camera, begin_date=start_date, end_date=end_date)

    df = pd.DataFrame(list(outputs))

    tooltips = [
        ('Exposure', '@exposure_id'),
        ('camera', '@camera'),
        ('Date', '@datef'),
    ]
    colors = [
        'red',
        'blue',
        'green',
        'orange'
    ]
    plot = hv.Curve([])
    hover = HoverTool(tooltips=tooltips)
    if amp != None:
        for amp in amp.split(','):
            idx = int(amp)-1
            amp_name = "AMP {}".format(amp)
            df[amp_name] = df['value'].apply(lambda x: x[idx])
            if DATASHADE == 'true':
                plot = plot * datashade(hv.Curve(df, ['mjd', amp_name], ['exposure_id', 'camera',
                                                                         'datef', 'dateobs'], label=amp_name))
            else:
                plot = plot * hv.Curve(df, ['mjd', amp_name], ['exposure_id', 'camera',
                                                               'datef', 'dateobs'], label=amp_name)
                points = hv.Points(df, ['mjd', amp_name], ['exposure_id', 'camera',
                                                           'datef', 'dateobs'], label=amp_name).opts(tools=[hover], size=2.5)
                plot = plot*points
    else:
        df[yaxis] = df['value'].apply(lambda x: x[0])
        plot = hv.Curve(df, ['mjd', yaxis], ['exposure_id', 'camera',
                                             'datef', 'dateobs'], label=yaxis)
        if DATASHADE == 'true':
            plot = datashade(plot)
        else:
            points = hv.Points(df, ['mjd', yaxis], ['exposure_id', 'camera',
                                                    'datef', 'dateobs'], label=yaxis).opts(tools=[hover], size=3)
            plot = plot*points
    layout = plot.redim.label(x='mjd', y=yaxis).opts(
        sizing_mode='scale_width', height=100, padding=0.1, fontsize='1.2vw')
    doc = renderer.server_doc(layout)
    doc.title = 'Time Series'
except Exception as e:
    print(e)
    sys.exit()
