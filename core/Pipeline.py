"""Optional item-processing pipeline."""


class pipeline:
    def __init__(self, stages=None):
        self.stages = []
        for stage in stages or []:
            self.add_stage(stage)

    def add_stage(self, stage):
        if not callable(stage) and not callable(getattr(stage, "process_item", None)):
            raise TypeError("(C31) a pipeline stage must be callable or define process_item")
        self.stages.append(stage)
        return self

    add_state = add_stage

    def process_item(self, item):
        current = item
        for stage in self.stages:
            current = getattr(stage, "process_item", stage)(current)
            if current is None:
                return None
        return current


Pipeline = pipeline
