
## BackBlaze python library


### How to use it

Just import B2 form backblaze_utils and set you parameters

```
from backblaze_utils import B2

b2 = B2()

b2.B2_ACCOUNT_ID = <YOUR ACCOUNT ID>
b2.B2_APPLICATION_KEY = <YOUR APPLICATION KEY>
b2.bucket_id = <YOUR BUCKET ID>
b2.b2_url_base = 'https://f001.backblazeb2.com/file/<BUCKET NAME>/'

``` 