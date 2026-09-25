from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, MultipleFileField
from wtforms.validators import Optional


class dropdown(FlaskForm):
    # Comma-separated yfinance tickers, e.g. "AAPL, MSFT, RELIANCE.NS"
    # Kept the class/field names (dropdown/ticker/upload/submit) so
    # existing templates and basic.py keep working.
    ticker = StringField(
        "Tickers (comma-separated yfinance symbols)",
        validators=[Optional()],
        render_kw={"placeholder": "e.g. AAPL, MSFT, RELIANCE.NS", "size": 60},
    )
    upload = MultipleFileField(render_kw={"multiple": True})
    submit = SubmitField("Submit")
