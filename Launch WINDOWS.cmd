pip install -r r.txt
cd sources
%@Try%
  python main.py
%@EndTry%
:@Catch
  python3 main.py
:@EndCatch