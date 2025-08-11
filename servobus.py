import scservo_sdk

class ServoBus:
	def __init__(self):
		self.port_handler_ = None
		self.end_ = 0

	def open(self, port_name):
		if self.port_handler_ is not None:
			return False
		handler = scservo_sdk.PortHandler(port_name)
		if handler.openPort():
			self.port_handler_ = handler
		return self.port_handler_ is not None

	def is_open(self):
		return self.port_handler_ is not None

	def close(self):
		self.port_handler_.closePort()
		self.port_handler_ = None

	def set_baudrate(self, baudrate):
		return self.port_handler_.setBaudRate(baudrate)
	
	def set_timeout(self, t):
		self.port_handler_.setPacketTimeoutMillis(t)
		
	def ping(self, id):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		model, result, error = packet_handler.ping(id)
		return result

	def read_model_number(self, id):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		model, result, error = packet_handler.ping(id)
		return model

	def set_end(self, end):
		self.end_ = end

	def read_byte(self, id, address):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		data, result, error = packet_handler.read1ByteTxRx(id, address)
		if result == 0:
			return data

	def read_word(self, id, address):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		data, result, error = packet_handler.read2ByteTxRx(id, address)
		if result == 0:
			return data

	def write_byte(self, id, address, value):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result, error = packet_handler.write1ByteTxRx(id, address, value)
		return result

	def write_word(self, id, address, value):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result, error = packet_handler.write2ByteTxRx(id, address, value)
		return result

	def write(self, id, address, buffer):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result, error = packet_handler.writeTxRx(id, address, len(buffer), buffer)
		return result

	def reg_write_action(self, id):
		packet_handler = scservo_sdk.protocol_packet_handler(self.port_handler_, self.end_)
		result = packet_handler.action(id)
		return result