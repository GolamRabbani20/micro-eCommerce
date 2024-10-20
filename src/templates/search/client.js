const searchClient = algoliasearch('GTFNIG7UXS', 'bd1b2afa77c63346d3460aa943023e8e');

const search = instantsearch({
  indexName: 'gro_Product',
  searchClient,
});

search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
  }),

  instantsearch.widgets.hits({
    container: '#hits',
  })
]);

search.start();
