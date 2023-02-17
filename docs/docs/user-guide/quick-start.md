Quick Start
------------
Import the API class for the Twitter API by writing:

```python
from pysna.api import TwitterAPI
```

or import utility functions, too, by writing:

```python
from pysna import *
```

Then, create an API instance by running:

```python
api = TwitterAPI("BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
```

and invoke a function:

```python
api.user_info(...)
```

Find usage and output examples in the [examples folder](https://github.com/mathun3003/PySNA/tree/main/examples).
