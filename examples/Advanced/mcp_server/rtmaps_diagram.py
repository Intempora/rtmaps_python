import xml.etree.ElementTree as ET


RTMAPS_XMLNS=r"{http://schemas.intempora.com/RTMaps/2011/RTMapsFiles}"

RTMAPS_TYPE_BOOL  = 0
RTMAPS_TYPE_INT   = 1
RTMAPS_TYPE_FLOAT = 2
RTMAPS_TYPE_STR   = 3
RTMAPS_TYPE_ENUM  = 4


RTMAPS_SUBTYPE_FILE       = 16
RTMAPS_SUBTYPE_PATH       = 32
RTMAPS_SUBTYPE_MUST_EXIST = 64


def _parent_component_node(xml_root, prop_or_input_or_output_node):
    if not prop_or_input_or_output_node:
        return None
    if "LongName" not in prop_or_input_or_output_node.attrib:
        raise ValueError(f"Node {_serialize_etree(prop_or_input_or_output_node)} should have attribute LongName.")
    long_name = prop_or_input_or_output_node.attrib["LongName"]
    comp_name = long_name.split(".")[0]
    if comp_name == "Engine":
        return None
    return _component_by_name(xml_root, comp_name)


def _component_by_name(xml_root, name: str):
    return xml_root.find(f".//{RTMAPS_XMLNS}Component[@Name='{name}']")


def _instances_of_component(xml_root, component):
    return xml_root.findall(f".//{RTMAPS_XMLNS}Component[@Model='{component}']")


def _all_components(xml_root):
    return xml_root.findall(f".//{RTMAPS_XMLNS}Component")


def _get_instance_name(component_node):
    return component_node.attrib["InstanceName"]


def _get_input_nodes(component_node):
    return component_node.findall(f"./{RTMAPS_XMLNS}Input")


def _get_output_nodes(component_node):
    return component_node.findall(f"./{RTMAPS_XMLNS}Output")


def _get_input_name(input_node):
    return input_node.attrib["LongName"]


def _all_properties(xml_root) -> list:
    return xml_root.findall(f".//{RTMAPS_XMLNS}Property")


def _get_output_connected_to_input(xml_root, input_node):
    input_name = _get_input_name(input_node)
    connection = xml_root.find(f".//{RTMAPS_XMLNS}Connection[@Input='{input_name}']")
    if connection is None:
        return None
    output_name = connection.attrib["Output"]
    return xml_root.find(f".//{RTMAPS_XMLNS}Output[@LongName='{output_name}']")


comp_id = 0
def _get_new_component_id(xml_root, model):
    # Generate the first name like Component_N that is not taken
    global comp_id
    while True:
        comp_id += 1
        comp_name = f"{model}_{comp_id}"
        if xml_root.find(f".//{RTMAPS_XMLNS}Component[@InstanceName='{comp_name}']") is None:
            return comp_name


def _create_component(xml_root, model, version="1.0"):
    comp = ET.SubElement(xml_root.find("."), f"{RTMAPS_XMLNS}Component")
    comp.attrib["Model"] = model
    comp.attrib["InstanceName"] = _get_new_component_id(xml_root, model)
    comp.attrib["Version"] = version
    return comp


def _add_input(component_node, name):
    component_name = _get_instance_name(component_node)
    long_name = f"{component_name}.{name}"
    input_node = ET.SubElement(component_node, f"{RTMAPS_XMLNS}Input")
    input_node.attrib["Name"] = name
    input_node.attrib["LongName"] = long_name
    return input_node


def _add_output(component_node, name):
    component_name = _get_instance_name(component_node)
    long_name = f"{component_name}.{name}"
    output_node = ET.SubElement(component_node, f"{RTMAPS_XMLNS}Output")
    output_node.attrib["Name"] = name
    output_node.attrib["LongName"] = long_name
    return output_node


def _add_connection(xml_root, output_node, input_node):
    conn = ET.SubElement(xml_root.find("."), f"{RTMAPS_XMLNS}Connection")
    conn.attrib["Output"] = output_node.attrib["LongName"]
    conn.attrib["Input"] = input_node.attrib["LongName"]
    return conn


def _add_property(node, name, type_str, val):
    # Find the current node's long name
    if "InstanceName" in node.attrib:
        parent_long_name = node.attrib["InstanceName"]
    elif "LongName" in node.attrib:
        parent_long_name = node.attrib["LongName"]
    else:
        raise ValueError("Cannot add property to node without InstanceName or LongName attribute")

    prop = ET.SubElement(node, f"{RTMAPS_XMLNS}Property")
    prop.attrib["LongName"] = f"{parent_long_name}.{name}"
    prop.attrib["Type"] = type_str
    prop.text = str(val)
    return prop


def _get_property_node(component_node, property_name):
    for child in component_node:
        if child.tag == f"{RTMAPS_XMLNS}Property":
            if "LongName" in child.attrib:
                if child.attrib["LongName"].endswith(f".{property_name}"):
                    return child
    return None


def _indent(elem, level=0):
    i = "\n" + level*"  "
    j = "\n" + (level-1)*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            _indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def _serialize_etree(xml_root):
    if xml_root is None:
        return ""

    # Patch etree's strange behavior: remove ns0 namespace
    new_xml = ET.tostring(_indent(xml_root.find(".")), encoding="unicode")
    new_xml = new_xml.replace("ns0:", "")
    new_xml = new_xml.replace("xmlns:ns0", "xmlns")
    return new_xml


class Diagram:
    """
    An RTMaps diagram
    This cannot be created from nothing, and needs to be initialized with `read_file`
    """
    root = None

    # Read or write file

    def read_file(self, path: str):
        """
        Read a diagram file
        """
        self.root = ET.ElementTree()
        self.root.parse(path)

    def write_file(self, path: str):
        """
        Write the diagram to a file
        """
        s = _serialize_etree(self.root)
        with open(path, "w") as f:
            f.write(s)

    # Packages

    def get_required_packages(self) -> list:
        """
        Get a list of Package objects representing the required packages listed in the diagram
        """
        nodes = self.root.findall(f".//{RTMAPS_XMLNS}RequiredPackages/{RTMAPS_XMLNS}File")
        packages = []
        for node in nodes:
            p = Package()
            p.diag = self
            p.node = node
            packages.append(p)
        return packages

    # Components

    def get_components(self, model="") -> list:
        """
        Get a list of Component objects representing the components listed in the diagram.
        If `model` is specified, get only the components of the specified model
        """
        if model:
            nodes = _instances_of_component(self.root, model)
        else:
            nodes = _all_components(self.root)

        comps = []
        for node in nodes:
            c = Component()
            c.diag = self
            c.node = node
            comps.append(c)
        return comps


    def get_component(self, name):
        """
        Get a component by name
        """
        node = _component_by_name(self.root, name)
        if not node:
            return None
        c = Component()
        c.diag = self
        c.node = node
        return c


    def add_component(self, model, version="1.0"):
        """
        Create a new component of the specified model
        """
        c = Component
        c.diag = self
        c.node = _create_component(self.root, model, version)
        return c


    # Properties

    def get_properties(self):
        """
        Get a list of Property objects representing all the properties in the diagram.
        These include all components' properties as well as Engine properties
        """
        components = dict()
        props = []
        for prop in _all_properties(self.root):
            # Find component in diagram
            comp_node = _parent_component_node(self.root, prop)
            if comp_node:
                comp_name = _get_instance_name(comp_node)
                if comp_name in components:
                    comp = components[comp_name]
                else:
                    new_comp = Component()
                    new_comp.diag = self
                    new_comp.node = comp_node
                    components[comp_name] = new_comp
                    comp = new_comp
            else:
                comp = None  # Engine properties

            # Append property
            p = Property()
            p.comp = comp
            p.node = prop
            props.append(p)

        return props


class _WithProperties:
    """
    Interface for elements that have Property children
    """
    node = None

    def set_property(self, name: str, val, type_val: int = -1):
        """
        Add/set a property by specifying its name, type and value.
        Type should be one of the RTMAPS_TYPE_XYZ constants
        The new Property object is returned

        If the property already exists, it is returned instead. Therefore, it can be a safer
        way to set a property that get_property(name).set_value(val)
        """
        preexisting = self.get_property(name)
        if preexisting:
            preexisting.set_value(val)
            return

        # Try to guess type_val
        if type_val == -1:
            if isinstance(val, int):
                type_val = RTMAPS_TYPE_INT
            elif isinstance(val, float):
                type_val = RTMAPS_TYPE_FLOAT
            elif isinstance(val, bool):
                type_val = RTMAPS_TYPE_BOOL
            elif isinstance(val, str):
                type_val = RTMAPS_TYPE_ENUM if "|" in val else RTMAPS_TYPE_STR
            else:
                raise ValueError(f"Cannot guess RTMaps type for {val} ({type(val)})")

        p = Property()
        p.comp = self
        p.node = _add_property(self.node, name, str(type_val), str(val))
        return

    def get_property(self, name: str):
        """
        Get a property by name.
        Returns None if the property does not exist
        """
        p = Property()
        p.comp = self
        p.node = _get_property_node(self.node, name)
        return p if p.node is not None else None

    def has_property(self, name: str):
        """
        Get whether a property of the specified name exists
        """
        return _get_property_node(self.node, name) is not None

    def remove_property(self, name: str):
        """
        Remove a property
        """
        for child in self.node:
            if "LongName" in child.attrib and child.attrib["LongName"].endswith(f".{name}"):
                self.node.remove(child)


class _WithNameAndLongName:
    """
    Interface for elements that have a Name and a LongName attribute
    """
    comp = None
    node = None

    def get_name(self):
        """
        Get the name of the element
        """
        return self.node.attrib["Name"] if "Name" in self.node.attrib else ""

    def get_long_name(self):
        """
        Get the long name of the element
        """
        return self.node.attrib["LongName"] if "LongName" in self.node.attrib else ""


class _WithType:
    """
    Interface for elements that have a Type and/or SubType attribute
    """
    comp = None
    node = None

    # Type

    def set_type(self, type_val):
        """
        Set the type of the element. Type should be one of the RTMAPS_TYPE_XYZ constants
        """
        self.node.attrib["Type"] = type_val

    def get_type(self) -> int:
        """
        Get the type of the element. Type is be one of the RTMAPS_TYPE_XYZ constants
        """
        return int(self.node.attrib["Type"]) if "Type" in self.node.attrib else 0

    def get_subtype(self) -> int:
        """
        Set the subtype of the element. SubType is a bitwise OR of the RTMAPS_SUBTYPE_XYZ constants
        """
        return int(self.node.attrib["SubType"]) if "SubType" in self.node.attrib else 0

    def is_int(self) -> bool:
        """
        Get whether the element is of type integer
        """
        return self.get_type() == RTMAPS_TYPE_INT

    def is_float(self) -> bool:
        """
        Get whether the element is of type float
        """
        return self.get_type() == RTMAPS_TYPE_FLOAT

    def is_str(self) -> bool:
        """
        Get whether the element is of type string
        """
        return self.get_type() == RTMAPS_TYPE_STR

    def is_bool(self) -> bool:
        """
        Get whether the element is of type boolean
        """
        return self.get_type() == RTMAPS_TYPE_BOOL

    def is_enum(self) -> bool:
        """
        Get whether the element is of type enumeration
        """
        return self.get_type() == RTMAPS_TYPE_ENUM

    def is_file(self) -> bool:
        """
        Get whether the element has subtype file
        """
        return bool(self.get_subtype() & RTMAPS_SUBTYPE_FILE)

    def is_path(self) -> bool:
        """
        Get whether the element has subtype path
        """
        return bool(self.get_subtype() & RTMAPS_SUBTYPE_PATH)

    def is_must_exist(self) -> bool:
        """
        Get whether the element has subtype must_exist
        """
        return bool(self.get_subtype() & RTMAPS_SUBTYPE_MUST_EXIST)


class Package:
    """
    A required package listed in the diagram
    """
    diag = None
    node = None

    def get_path(self) -> str:
        """
        Get the path to the required package
        """
        return self.node.text.strip() if self.node.text else ""

    def set_path(self, path: str):
        """
        Set the path to the required package
        """
        self.node.text = path

    def get_version(self) -> str:
        """
        Get the required version, or an empty string if none is specified
        """
        return self.node.attrib["Version"] if "Version" in self.node.attrib else ""

    def set_version(self, version: str):
        """
        Set the required version
        """
        self.node.attrib["Version"] = version


class Component(_WithProperties):
    """
    A component in the diagram
    """
    diag = None
    node = None

    # Name

    def get_name(self) -> str:
        """
        Get the name (instance name) of the component
        """
        return _get_instance_name(self.node)

    def get_model_name(self) -> str:
        """
        Get the name of the model of the component
        """
        return self.node.attrib["Model"] if "Model" in self.node.attrib else ""

    # Inputs and outputs

    def get_inputs(self) -> list:
        """
        Get a list of Input objects representing the inputs of the component
        """
        nodes = _get_input_nodes(self.node)
        inputs = []
        for node in nodes:
            i = Input()
            i.comp = self
            i.node = node
            inputs.append(i)
        return inputs

    def get_input(self, name: str):
        """
        Get the input of the specified name. If none exists, create and return the input.
        """
        # Try to find input
        inputs_with_name = [i for i in self.get_inputs() if i.get_name() == name]
        if inputs_with_name:
            return inputs_with_name[0]

        # Create input
        new_input = Input()
        new_input.comp = self
        new_input.node = _add_input(self.node, name)
        return new_input

    def get_outputs(self) -> list:
        """
        Get a list of Output objects representing the outputs of the component
        """
        nodes = _get_output_nodes(self.node)
        outputs = []
        for node in nodes:
            o = Output()
            o.comp = self
            o.node = node
            outputs.append(o)
        return outputs

    def get_output(self, name: str):
        """
        Get the output of the specified name. If none exists, create and return the output.
        """
        # Try to find output
        outputs_with_name = [o for o in self.get_outputs() if o.get_name() == name]
        if outputs_with_name:
            return outputs_with_name[0]

        # Create output
        new_output = Output()
        new_output.comp = self
        new_output.node = _add_output(self.node, name)
        return new_output


class Output(_WithNameAndLongName, _WithType, _WithProperties):
    """
    An output of a component
    """
    comp = None
    node = None

    def connect(self, inp):
        """
        Connect the output to an Input object
        """
        _add_connection(self.comp.diag.root, self.node, inp.node)


class Input(_WithNameAndLongName, _WithType, _WithProperties):
    comp = None
    node = None

    def connect(self, out):
        """
        Connect the input to an Output object. (Data goes from the output to the input)
        """
        out.connect(self)

    def get_connected_outputs(self):
        """
        Get a list of Output objects representing all component outputs connected to the input
        """
        node = _get_output_connected_to_input(self.comp.diag.root, self.node)
        if not node:
            return None
        if "LongName" not in node.attrib:
            raise ValueError(f"Node {_serialize_etree(node)} should have attribute LongName.")
        long_name = node.attrib["LongName"]
        comp_name = long_name.split(".")[0]

        o = Output()
        o.comp = self.comp.diag.get_component(comp_name)
        o.node = node
        return o


class Property(_WithNameAndLongName, _WithType):
    """
    A property of a component, or a property of the Engine
    """

    comp = None  # If this is an Engine property, comp is None
    node = None

    # Getters

    def has_value(self) -> str:
        """
        Get whether the property has a value
        """
        return self.node.text is not None

    def get_value(self, strip=True) -> str:
        """
        Get the value of the property as a string
        """
        t = self.node.text
        val = t if t else ""
        return val.strip() if strip else val

    def get_value_int(self) -> int:
        """
        Get the value of the property as an integer
        """
        return int(self.get_value())

    def get_value_float(self) -> float:
        """
        Get the value of the property as a float
        """
        return float(self.get_value())

    def get_value_bool(self) -> bool:
        """
        Get the value of the property as a bool
        """
        return bool(self.get_value())

    def get_value_relative(self, strip=True):
        """
        For paths: Get the relative version of the path
        """
        rel_node = self.node.find(f"{RTMAPS_XMLNS}Relative")
        val = rel_node.text if rel_node else ""
        return val.strip() if strip else val

    # Setters

    def set_value(self, value):
        """
        Set the value of the property
        """
        self.node.text = str(value)
