import smbus

I2C_CHAN = 0
I2C_SWITCH_ADDR = 0x70
I2C_SWITCH_BUS = 0
GPIO_ADDR = 0x23
GPIO_PINS = [0, 5, 3, 4, 12, 1, 6, 8, 9, 13]

bus = smbus.SMBus(I2C_CHAN)

print('Setting I2C bus to %d' % I2C_SWITCH_BUS)
bus.write_byte(I2C_SWITCH_ADDR, 1<<I2C_SWITCH_BUS)
print('I2C control register is %d' % bus.read_byte(I2C_SWITCH_ADDR))

print('Reading address %d' % GPIO_ADDR)
for cb in range(8):
    print(cb, '0x%x' % bus.read_i2c_block_data(GPIO_ADDR, cb, 1)[0])

# Set pins of interest to outputs
R0 = 0b10000100
R1 = 0b11001100
bus.write_i2c_block_data(GPIO_ADDR, 0x06, [R0])
bus.write_i2c_block_data(GPIO_ADDR, 0x07, [R1])

