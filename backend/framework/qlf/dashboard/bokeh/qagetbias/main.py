import sys

from bokeh.plotting import Figure
from bokeh.layouts import row, column, widgetbox, gridplot

from bokeh.io import curdoc
from bokeh.io import output_notebook, show, output_file

from bokeh.models.widgets import PreText, Div
from bokeh.models import HoverTool, ColumnDataSource, PrintfTickFormatter
from bokeh.models import (LinearColorMapper ,    ColorBar)


from bokeh.palettes import ( Colorblind, Viridis256)

from bokeh.io import output_notebook
import numpy as np

from dashboard.bokeh.helper import get_url_args, write_description, write_info,\
            get_merged_qa_scalar_metrics, eval_histpar, get_palette  
from dashboard.bokeh.qlf_plot import alert_table, metric_table, mtable

import numpy as np
import logging
from bokeh.resources import CDN
from bokeh.embed import file_html
logger = logging.getLogger(__name__)


class Bias:
    def __init__(self, process_id, arm, spectrograph):
            self.selected_process_id = process_id
            self.selected_arm = arm
            self.selected_spectrograph = spectrograph

    def load_qa(self):
        cam = self.selected_arm+str(self.selected_spectrograph)
        try:
            mergedqa = get_merged_qa_scalar_metrics(self.selected_process_id, cam)
            check_ccds = mergedqa['TASKS']['CHECK_CCDs']
            getbias =  check_ccds['METRICS']# metrics['getrms']

            nrg = check_ccds['PARAMS']['BIAS_AMP_NORMAL_RANGE']
            wrg = check_ccds['PARAMS']['BIAS_AMP_WARN_RANGE']
            tests =  mergedqa['TASKS']['CHECK_CCDs']['PARAMS']


        except Exception as err:
            logger.info(err)
            sys.exit
 
        # ============================================
        # THIS: Given the set up in the block above, 
        #       we have the bokeh plots

        # Get Bias
        name = 'BIAS_AMP'
        metr = getbias

        dx = [0,1,0,1]
        dy = [1,1,0,0]
        dz = metr[name] #getbias['BIAS_AMP']


        Reds = get_palette("Reds")
        mapper = LinearColorMapper(palette= Reds, low=min(dz),high=max(dz) )

        dzmax, dzmin = max(dz), min(dz) 
        if np.log10(dzmax) > 4 or np.log10(dzmin) <-3:
            ztext = ['{:3.2e}'.format(i) for i in dz]
            cbarformat = "%2.1e"
        elif np.log10(dzmin)>0:
            ztext = ['{:4.3f}'.format(i) for i in dz]
            cbarformat = "%4.2f"
        else:
            ztext = ['{:5.4f}'.format(i) for i in dz]
            cbarformat = "%5.4f"


        source = ColumnDataSource(
            data=dict(
                x=dx,
                y=dy,
                y_offset1 = [i+0.15 for i in dy],
                y_offset2 = [i-0.05 for i in dy],

                z = dz,
                amp = ['AMP %s'%i for i in range(1,5) ] ,
                ztext = ztext#['{:3.2e}'.format(i) for i in dz]
            )
        )

        cmap_tooltip = """
            <div>
                <div>
                    <span style="font-size: 12px; font-weight: bold; color: #303030;">counts: </span>
                    <span style="font-size: 13px; color: #515151">@z</span>
                </div>
                <div>
                    <span style="font-size: 12px; font-weight: bold; color: #303030;">AMP: </span>
                    <span style="font-size: 13px; color: #515151;">@amp</span>
                </div>
            </div>
        """.replace("counts:", name+":")

        hover = HoverTool(tooltips=cmap_tooltip)

        p = Figure(title=name, tools=[hover, "save"],
                x_range= list([-0.5,1.5]),           # length = 18
                y_range= list([-0.5,1.5]), #numeros romanos
                plot_width=450, plot_height=400
                )


        p.grid.grid_line_color = None
        p.outline_line_color = None
        p.axis.clear

        text_props = {
            "source": source,
            "angle": 0,
            "color": "black",
            "text_color":"black",
            "text_align": "center",
            "text_baseline": "middle"
        }

        p.xaxis.axis_label="Average bias value per Amp (photon counts)"

        p.rect("x", "y", .98, .98, 0, source=source,
            fill_color={'field': 'z', 'transform': mapper}, fill_alpha=0.9)#, color="color")
        p.axis.minor_tick_line_color=None

        p.text(x="x", y="y_offset2", text="ztext",
            text_font_style="bold", text_font_size="20pt", **text_props)
        p.text(x="x", y="y_offset1", text="amp",
                text_font_size="18pt", **text_props)
        formatter = PrintfTickFormatter(format=cbarformat)#format='%2.1e')
        color_bar = ColorBar(color_mapper=mapper,  major_label_text_align='left',
                        major_label_text_font_size='10pt', label_standoff=2, location=(0, 0)
                        ,formatter=formatter, title="", title_text_baseline="alphabetic" )

        p.add_layout(color_bar, 'right')


        p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
        p.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
        p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
        p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks

        p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks

        info, nlines = write_info('getbias', tests)
        try:
            info_hist ="""
            <p style="font-size:18px;"> BIAS: {} </p>
            """.format(getbias['BIAS'])
        except:
            info_hist=""""""
        txt = Div(text=info_hist, width= 2*p.plot_width)

        from dashboard.bokeh.qlf_plot import html_table

        
        tb = html_table( nrng=nrg, wrng=wrg  )
        tbinfo=Div(text=tb, width=400)

        info_col=Div(text=write_description('getbias'), width=2*p.plot_width)

        # Prepare tables
        comments='Value of bias averaged over each amplifier'
        metricname='BIAS_AMP'
        keyname='getbias'
        curexp=mergedqa['TASKS']['CHECK_CCDs']['METRICS']['LITFRAC_AMP']
        refexp=mergedqa['TASKS']['CHECK_CCDs']['PARAMS']['BIAS_AMP_REF']
        metric_txt=metric_table(metricname, comments, keyname,  curexp=curexp, refexp=refexp )
        metric_txt=mtable('getbias', mergedqa, comments )
        metric_tb=Div(text=metric_txt, width=350)

        alert_txt = alert_table(nrg,wrg)
        alert_tb = Div(text=alert_txt, width=350)

        ptxt = column(widgetbox(info_col, css_classes=["header"]), Div(),
                        widgetbox(metric_tb),widgetbox(alert_tb),
                        p,
                        css_classes=["display-grid"])  # ,p_hist)


        # End of Bokeh Block
        return file_html(ptxt, CDN, "GETBIAS")
