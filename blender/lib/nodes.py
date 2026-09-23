"""Tiny helpers to keep shader-node code readable."""
import bpy


class Graph:
    def __init__(self, tree):
        self.t = tree
        self.n = tree.nodes
        self.l = tree.links

    def node(self, kind, **props):
        nd = self.n.new(kind)
        for k, v in props.items():
            if k.startswith("in_"):
                nd.inputs[k[3:].replace("_", " ")].default_value = v
            else:
                setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.l.new(a, b)
        return b

    def math(self, op, a, b=None, clamp=False):
        nd = self.node("ShaderNodeMath", operation=op, use_clamp=clamp)
        self._feed(nd.inputs[0], a)
        if b is not None:
            self._feed(nd.inputs[1], b)
        return nd.outputs[0]

    def mix(self, fac, a, b, blend="MIX"):
        nd = self.node("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        self._feed(nd.inputs["Factor"], fac)
        self._feed(nd.inputs["A"], a)
        self._feed(nd.inputs["B"], b)
        return nd.outputs["Result"]

    def maprange(self, v, fmin, fmax, tmin=0.0, tmax=1.0, smooth=False):
        nd = self.node("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if smooth else "LINEAR")
        self._feed(nd.inputs["Value"], v)
        nd.inputs["From Min"].default_value = fmin
        nd.inputs["From Max"].default_value = fmax
        nd.inputs["To Min"].default_value = tmin
        nd.inputs["To Max"].default_value = tmax
        return nd.outputs["Result"]

    def ramp(self, v, stops):
        """stops: [(pos, (r, g, b)), ...]"""
        nd = self.node("ShaderNodeValToRGB")
        els = nd.color_ramp.elements
        while len(els) < len(stops):
            els.new(0.5)
        for el, (pos, rgb) in zip(els, stops):
            el.position = pos
            el.color = (*rgb, 1.0)
        self._feed(nd.inputs[0], v)
        return nd.outputs[0]

    def noise(self, vec, scale, detail=2.0, rough=0.5, dist=0.0):
        nd = self.node("ShaderNodeTexNoise", in_Scale=scale, in_Detail=detail, in_Roughness=rough, in_Distortion=dist)
        if vec is not None:
            self._feed(nd.inputs["Vector"], vec)
        return nd

    def voronoi(self, vec, scale, feature="F1"):
        nd = self.node("ShaderNodeTexVoronoi", feature=feature, in_Scale=scale)
        if vec is not None:
            self._feed(nd.inputs["Vector"], vec)
        return nd

    def combine(self, x, y, z):
        nd = self.node("ShaderNodeCombineXYZ")
        for sock, v in zip(nd.inputs, (x, y, z)):
            self._feed(sock, v)
        return nd.outputs[0]

    def xyz(self, vec):
        nd = self.node("ShaderNodeSeparateXYZ")
        self._feed(nd.inputs[0], vec)
        return nd.outputs

    def _feed(self, sock, v):
        if isinstance(v, bpy.types.NodeSocket):
            self.l.new(v, sock)
        elif isinstance(v, tuple) and len(v) == 3 and sock.type == "RGBA":
            sock.default_value = (*v, 1.0)
        else:
            sock.default_value = v


def material(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    g = Graph(m.node_tree)
    return m, g, g.n["Principled BSDF"]
