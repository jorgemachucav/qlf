import sys

from bokeh.plotting import Figure
from bokeh.layouts import row, column, widgetbox, gridplot

from bokeh.io import curdoc
from bokeh.io import output_notebook, show, output_file

from bokeh.models.widgets import PreText, Div
from bokeh.models import HoverTool, ColumnDataSource, PrintfTickFormatter
from bokeh.models import (LinearColorMapper ,    ColorBar)

from dashboard.bokeh.qlf_plot import html_table, mtable, alert_table
from bokeh.palettes import (RdYlBu, Colorblind, Viridis256)

from bokeh.io import output_notebook
import numpy as np

from dashboard.bokeh.helper import get_url_args, write_description, write_info, get_merged_qa_scalar_metrics
from dashboard.bokeh.helper import get_palette
from dashboard.bokeh.qlf_plot import set_amp, plot_amp


import numpy as np
import logging
from bokeh.resources import CDN
from bokeh.embed import file_html
logger = logging.getLogger(__name__)


class RMS:
    def __init__(self, process_id, arm, spectrograph):
            self.selected_process_id = process_id
            self.selected_arm = arm
            self.selected_spectrograph = spectrograph

    def load_qa(self):
        cam = self.selected_arm+str(self.selected_spectrograph)

        try:
            mergedqa = get_merged_qa_scalar_metrics(self.selected_process_id, cam)
            check_ccds = mergedqa['TASKS']['CHECK_CCDs']
            getrms    =  check_ccds['METRICS']

            nrg = check_ccds['PARAMS']['NOISE_AMP_NORMAL_RANGE']
            wrg = check_ccds['PARAMS']['NOISE_AMP_WARN_RANGE']

        except Exception as err:
            logger.info(err)
            sys.exit('Could not load data')


        Reds = get_palette('Reds')

        # amp 1
        dz = getrms['NOISE_AMP']
        name = 'NOISE_AMP'

        mapper = LinearColorMapper(palette= Reds, low=min(dz),high=max(dz) )

        ztext, cbarformat = set_amp(getrms['NOISE_AMP'])
        p = plot_amp(dz, mapper,name=name)

        p.xaxis.axis_label = "NOISE per Amp"

        formatter = PrintfTickFormatter(format=cbarformat)
        color_bar = ColorBar(color_mapper=mapper,  major_label_text_align='left',
                        major_label_text_font_size='10pt', label_standoff=2, location=(0, 0),
                        formatter=formatter, title="", title_text_baseline="alphabetic" )
        p.add_layout(color_bar, 'right')


        # amp 2
        dz = getrms['NOISE_OVERSCAN_AMP']
        name = 'NOISE_OVERSCAN_AMP'

        mapper = LinearColorMapper(palette= Reds, low=min(dz),high=max(dz) )

        ztext, cbarformat = set_amp(dz)
        p2 = plot_amp(dz, mapper,name=name)

        p2.xaxis.axis_label = "NOISE Overscan per Amp"

        formatter = PrintfTickFormatter(format=cbarformat)
        color_bar = ColorBar(color_mapper=mapper,  major_label_text_align='left',
                        major_label_text_font_size='10pt', label_standoff=2, location=(0, 0),
                        formatter=formatter, title="", title_text_baseline="alphabetic" )
        p2.add_layout(color_bar, 'right')


        tb = html_table( nrng=nrg, wrng=wrg  )
        tbinfo=Div(text=tb, width=400)


        info, nlines = write_info('getrms', check_ccds['PARAMS'])
        info= """<div> 
        <body><p  style="text-align:left; color:#262626; font-size:20px;">
                    <b>Get RMS</b> <br>Used to calculate RMS of region of 2D image, including overscan.</body></div>"""
        nlines=2
        txt = Div(text=info, width=p.plot_width)
        info_col=Div(text=write_description('getrms'))


        # Prepare tables
        comments='value of RMS for each amplifier read directly from the header of the pre processed image'
        refexp=mergedqa['TASKS']['CHECK_CCDs']['PARAMS']['BIAS_AMP_REF']
        metric_txt=mtable('getbias', mergedqa, comments )
        metric_tb=Div(text=metric_txt, width=350)

        alert_txt = alert_table(nrg,wrg)
        alert_tb = Div(text=alert_txt, width=350)

        layout = column(widgetbox(info_col, css_classes=["header"]), Div(),
            widgetbox(metric_tb),widgetbox(alert_tb),
            p,
            p2,
            css_classes=["display-grid"])

        return file_html(layout, CDN, "GETRMS")
