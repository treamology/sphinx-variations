# sphinx-variations

A Sphinx extension that allows project maintainers to create multiple variations of their documentation, based on its usage of the `.. only` directive. Each variation contains a Sphinx tag and a friendly name.

## How to Use

### Installing
sphinx-variations is available on PyPi:

```
python3 -m pip install sphinx-variations
```

After installing the package, list the extension in your Sphinx project's `conf.py`.

```
extensions = [..., 'variations']
```

### Configuration

To create multiple variations for your docs, a list of tags to use as variations can be inserted into your `conf.py` file:

```
variations = [( [tagname], [friendly name] )]
```

For example:

```
variations = [('python', 'Python'),
              ('cpp', 'C++')]
```

The above will cause two copies of the documentation text to be made, each in a directory with the tag name. Static files are not copied between the two variations, but are shared between them.

### Template Variables
This extension also provides two template variables, `variations` and `currentvariation`.

`variations` contains the complete list of variations in the same format specified above, and `currentvariation` contains the tuple for the current variation.

These variables can be used to create links between the different variations of your documentation, for example.

# License
MIT, see `LICENSE`.