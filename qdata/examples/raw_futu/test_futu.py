from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, is_encrypt=False)
quote_ctx.close() # After using the connection, remember to close it to prevent the number of connections from running out
