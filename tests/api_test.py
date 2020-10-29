import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('../'))

# launch test command from this folder: pytest -s -v

from API import ptsapi

def test_get_ticker_id():
   id = ptsapi.get_ticker_id('GAZP')
   assert id > 0


def test_create_post():
   postdata = {'post': {'analysis_type_id': 1,
                        'ticker_id': ptsapi.get_ticker_id('GAZP'),
                        'date_analysis': datetime.now().strftime("%Y-%m-%d"),
                        'header': 'test post',
                        'content': 'test content',
                        'slug': 'aokjcds1123',
                        'slug_url': 'ezhednevnyj-analiz-{0}-ot-{1}-{2}-{3}'.format(
                                                   'GAZP'.lower(),
                                                   datetime.now().year,
                                                   datetime.now().month,
                                                   datetime.now().day),
                        'created': datetime.now().strftime("%Y-%m-%dT%H:%M"),
                        'sig_elder': 0,
                        'sig_channel': 0,
                        'sig_DivBar': 0,
                        'sig_NR4ID': 0,
                        'sig_breakVolatility': 0,
                        'sig_elder_proba': 0,
                        'sig_channel_proba': 0,
                        'sig_DivBar_proba': 0,
                        'sig_NR4ID_proba': 0,
                        'sig_breakVolatility_proba': 0
                        }
               }

   result = ptsapi.createpost(postdata)
   assert result != ''
