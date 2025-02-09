import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots


def plot_multiple_pie_chart(labels, values, subtitles):
    fig = make_subplots(rows=1, cols=len(values), subplot_titles=subtitles,
                        specs=[[{"type": "pie"} for i in range(len(values))]])

    i = 1
    for label, value, subtitle in zip(labels, values, subtitles):
        fig.add_trace(go.Pie(name=subtitle, labels=label, values=value,
                             hoverinfo='label+percent+value',
                             textinfo='label'), row=1, col=i)
        i += 1

    fig.update_layout(
        font=dict(family='Arial', size=12),
        margin=dict(
            l=70,
            r=70,
            t=70,
            b=70,
        ))
    div = plot(fig, output_type='div', auto_open=False, image_filename='plot_img')

    return div
