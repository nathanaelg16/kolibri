<template>

  <tr>
    <td>
      <KRouterLink
        :text="group.name"
        :to="$router.getRoute('GroupMembersPage', { groupId: group.id })"
        icon="group"
      />
    </td>
    <td>
      {{ $formatNumber(group.users.length) }}
    </td>
    <td class="core-table-button-col">
      <KButton
        hasDropdown
        appearance="flat-button"
        :text="coreString('optionsLabel')"
      >
        <template #menu>
          <KDropdownMenu
            :options="menuOptions"
            @select="handleSelection"
          />
        </template>
      </KButton>
    </td>
  </tr>

</template>


<script>

  import commonCoreStrings from 'kolibri.coreVue.mixins.commonCoreStrings';
  import commonCoach from '../../common';

  export default {
    name: 'GroupRow',
    mixins: [commonCoach, commonCoreStrings],
    props: {
      group: {
        type: Object,
        required: true,
        validator(group) {
          return group.name && group.users;
        },
      },
    },
    computed: {
      menuOptions() {
        return [this.coachString('renameAction'), this.coreString('deleteAction')];
      },
    },
    methods: {
      handleSelection(selectedOption) {
        let emitted;
        if (selectedOption === this.coachString('renameAction')) {
          emitted = 'rename';
        } else if (selectedOption === this.coreString('deleteAction')) {
          emitted = 'delete';
        }
        this.$emit(emitted, this.group.name, this.group.id);
      },
    },
  };

</script>


<style lang="scss" scoped>

  .icon {
    margin-right: 8px;
    vertical-align: middle;
  }

</style>
