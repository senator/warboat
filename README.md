# Warboat - Just you versus the computer in a classic maritime matchup

(c) 2022 Lebbeous Fogle-Weekley. Licensed to the public via GPLv2. See
[license](LICENSE).

## Why?

My daughter and I were talking about programming while we played the
familiar strategy board game on which this is based.  She asked me if I
could program a computer a battleship game, so of course I said something
like, "*pssh* in about an hour!"

It took more than 20 to really turn it into anything decent, and that's
assuming your definition of decent includes text-based interfaces meant
to be played from the command line. :-)

There is nothing *too* clever here.

## Dependencies

Just at the moment, install termcolor, whether from pip or from a distro
package like `python3-termcolor` in Ubuntu.

## TODO

- Clean up package layout / dependency listing.
- Remove Best of N match loop (who has the patience?)
- Don't assume Unicode-friendly terminal
- Generally improve the user interface's tidiness
