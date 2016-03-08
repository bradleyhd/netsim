import asyncio

from queue import Queue, Empty
from datetime import datetime
from threading import Thread

class Worker(Thread):

  def __init__(self):

    super().__init__()
    self.__proceed = True
    self.__queue = Queue()
    self.__loop = None
    self.limit_simultaneous_processes = None

  def stop(self):

    self.__proceed = False

  def run(self):

    self.__loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.__loop)

    self.limit_simultaneous_processes = asyncio.Semaphore(1)
    self.__loop.run_until_complete(self.process_updates())

  def enqueue(self, update, callback=None):
      self.__queue.put((update, callback))

  @asyncio.coroutine
  def process_updates(self):

    while self.__proceed:

      try:

        while True:

          update, callback = self.__queue.get_nowait()
          task = asyncio.async(update())

          if callback:
              task.add_done_callback(callback)

      except Empty as e:
          pass

      yield from asyncio.sleep(1)
