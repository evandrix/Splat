def main():

  def f(x):
    if x > 0:
      return x*x
    1/0

  for i in range(4, 9):
    if f(i) < 0: x=9
    if i == 8:
       continue
       print "Here"
    if i == 10:
       continue

  try:
      raise TypeError("Hi! %d" % "sdfa")
  except TypeError:
      pass

main()