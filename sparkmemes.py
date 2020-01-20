#!/usr/bin/env python3
from sys import argv
from datetime import date

if __name__ == "__main__":
  print(argv[1].replace('{}',str((date.today()-date(2020,1,20)).days)))

