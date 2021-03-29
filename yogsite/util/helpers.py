from yogsite.config import cfg


def yield_file_chunks(path):
	CHUNK_SIZE = 65536 # Yield the file in 8kb chunks
	with open(path, 'rb') as fd:
		while 1:
			buf = fd.read(CHUNK_SIZE)
			if buf:
				yield buf
			else:
				break