org.apache.hadoop.hbase.ExtendedCell

```

default int write(OutputStream out, boolean withTags) throws IOException {
  // Key length and then value length
  ByteBufferUtils.putInt(out, KeyValueUtil.keyLength(this));
  ByteBufferUtils.putInt(out, getValueLength());

  // Key
  PrivateCellUtil.writeFlatKey(this, out);

  if (getValueLength() > 0) {
    // Value
    out.write(getValueArray(), getValueOffset(), getValueLength());
  }

  // Tags length and tags byte array
  if (withTags && getTagsLength() > 0) {
    // Tags length
    out.write((byte)(0xff & (getTagsLength() >> 8)));
    out.write((byte)(0xff & getTagsLength()));

    // Tags byte array
    out.write(getTagsArray(), getTagsOffset(), getTagsLength());
  }

  return getSerializedSize(withTags);
}
```