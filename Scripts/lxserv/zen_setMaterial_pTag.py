#python

import lx, lxu, lxifc, modo, zen, traceback

NAME = zen.symbols.ARGS_NAME
MODE = zen.symbols.ARGS_MODE
OPERATION = zen.symbols.ARGS_OPERATION
CONNECTED = zen.symbols.ARGS_CONNECTED
PRESET = zen.symbols.ARGS_PRESET

AUTO_FILTER = zen.symbols.FILTER_TYPES_AUTO
MATERIAL = zen.symbols.FILTER_TYPES_MATERIAL
PART = zen.symbols.FILTER_TYPES_PART
PICK = zen.symbols.FILTER_TYPES_PICK

AUTO_OPERATION = zen.symbols.OPERATIONS_AUTO
ADD = zen.symbols.OPERATIONS_ADD
REMOVE = zen.symbols.OPERATIONS_REMOVE

NAME_CMD = zen.symbols.COMMAND_NAME_PTAG

# The UIValueHints object that returns the items in the list of commands
# to the form.
class sPresetText(lxifc.UIValueHints):
    def __init__(self, items):
        self._items = items

    def uiv_Flags(self):
        return lx.symbol.fVALHINT_POPUPS

    def uiv_PopCount(self):
        return len(self._items)

    def uiv_PopUserName (self, index):
        return self._items[index]

    def uiv_PopInternalName (self, index):
        return self._items[index]


class CMD_zen(lxu.command.BasicCommand):

    _last_used = ''

    def __init__(self):
        lxu.command.BasicCommand.__init__(self)
        self.dyna_Add(NAME, lx.symbol.sTYPE_STRING)
        self.dyna_Add(MODE, lx.symbol.sTYPE_STRING)
        self.dyna_Add(OPERATION, lx.symbol.sTYPE_STRING)
        self.dyna_Add(CONNECTED, lx.symbol.sTYPE_BOOLEAN)
        self.dyna_Add(PRESET, lx.symbol.sTYPE_STRING)

        for i in range(1,5):
            self.basic_SetFlags(i, lx.symbol.fCMDARG_OPTIONAL | lx.symbol.fCMDARG_HIDDEN)

    def cmd_Flags(self):
        return lx.symbol.fCMD_POSTCMD | lx.symbol.fCMD_MODEL | lx.symbol.fCMD_UNDO

    def cmd_DialogInit(self):
        if self._last_used != '':
            self.attr_SetString(0, self._last_used)
        elif len(zen.items.get_all_material_tags()) > 0:
            self.attr_SetString(0, zen.items.get_all_material_tags()[0])

    def arg_UIValueHints(self, index):
        if index == 0:
            return sPresetText(zen.items.get_all_material_tags())

    def arg_UIHints (self, index, hints):
        if index == 0:
            hints.Class ("sPresetText")

    @classmethod
    def set_last_used(cls, value):
        cls._last_used = value

    def basic_Execute(self, msg, flags):
        try:
            args = {}
            args[NAME] = self.dyna_String(0) if self.dyna_IsSet(0) else zen.defaults.get('ptag')
            args[MODE] = self.dyna_String(1) if self.dyna_IsSet(1) else AUTO_FILTER
            args[OPERATION] = self.dyna_String(2) if self.dyna_IsSet(2) else AUTO_OPERATION
            args[CONNECTED] = self.dyna_Bool(3) if self.dyna_IsSet(3) else False
            args[PRESET] = self.dyna_String(4) if self.dyna_IsSet(4) else None

            if args[OPERATION] != REMOVE:
                self.set_last_used(args[NAME])

            if args[NAME] == '':
                args[NAME] = zen.defaults.get('ptag')

            if args[MODE] == MATERIAL:
                LXi_POLYTAG = lx.symbol.i_POLYTAG_MATERIAL
            elif args[MODE] == PICK:
                LXi_POLYTAG = lx.symbol.i_POLYTAG_PICK
            else:
                LXi_POLYTAG = lx.symbol.i_POLYTAG_PART

            if args[OPERATION] == AUTO_OPERATION:
                if args[CONNECTED]:
                    zen.selection.tag_polys( args[NAME], True, LXi_POLYTAG )
                else:
                    zen.selection.tag_polys( args[NAME], False, LXi_POLYTAG )

                if (
                    not zen.shadertree.get_masks(pTags = {args[NAME]:LXi_POLYTAG})
                    and not args[NAME] == zen.defaults.get('ptag')
                    ):

                    mask = zen.shadertree.build_material(
                        i_POLYTAG = LXi_POLYTAG,
                        pTag = args[NAME],
                        preset = args[PRESET]
                    )

                    # zen.shadertree.cleanup()
                    zen.shadertree.move_to_base_shader(mask)

            if args[OPERATION] == ADD:
                if args[CONNECTED]:
                    zen.selection.tag_polys( args[NAME], True, LXi_POLYTAG )
                else:
                    zen.selection.tag_polys( args[NAME], False, LXi_POLYTAG )

                mask = zen.shadertree.build_material(
                    i_POLYTAG = LXi_POLYTAG,
                    pTag = args[NAME],
                    preset = args[PRESET]
                )

                # zen.shadertree.cleanup()
                zen.shadertree.move_to_base_shader(mask)

            if args[OPERATION] == REMOVE:
                if args[CONNECTED]:
                    zen.selection.tag_polys( zen.defaults.get('ptag'), True, LXi_POLYTAG )
                else:
                    zen.selection.tag_polys( zen.defaults.get('ptag'), False, LXi_POLYTAG )

                # zen.shadertree.cleanup()

        except:
            traceback.print_exc()


lx.bless(CMD_zen, NAME_CMD)